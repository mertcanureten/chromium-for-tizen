// Developer-only V8 execution probe. No networking, page access or credentials.
#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include "v8.h"
#include "libplatform/libplatform.h"
#include "ppapi/c/ppp.h"
#include "ppapi/c/ppp_instance.h"
#include "ppapi/c/ppp_messaging.h"
#include "ppapi/c/ppb_var.h"
#include "ppapi/c/ppb_messaging.h"
static const PPB_Var* vars;
static const PPB_Messaging* messaging;
static std::unique_ptr<v8::Platform> platform;
static PP_Instance active_instance;
static void post(PP_Instance i,const std::string& s){auto v=vars->VarFromUtf8(s.data(),s.size());messaging->PostMessage(i,v);vars->Release(v);}
static void oom(const char* where,const v8::OOMDetails& d){post(active_instance,std::string("OOM: ")+where+" "+(d.detail?d.detail:""));}
static void message(PP_Instance i,PP_Var input){
 if(input.type!=PP_VARTYPE_STRING)return;
 uint32_t len=0;const char* text=vars->VarToUtf8(input,&len);
 if(!text||len>16384){post(i,"ERROR: invalid source");return;}
 if(!platform){
  active_instance=i;
  v8::V8::SetFatalMemoryErrorCallback(oom);
  v8::V8::SetFatalErrorHandler([](const char* file,int line,const char* message){post(active_instance,std::string("FATAL: ")+message);});
  post(i,"STAGE: initialize V8");
  v8::V8::SetFlagsFromString("--single-threaded --jitless --no-expose-wasm --max-old-space-size=64");
  post(i,"STAGE: flags set");
  platform=v8::platform::NewSingleThreadedDefaultPlatform();
  post(i,"STAGE: platform created");
  v8::V8::InitializePlatform(platform.get());
  post(i,"STAGE: platform initialized");
  if(!v8::V8::Initialize()){post(i,"ERROR: V8 initialize");return;}
 }
 post(i,std::string("VERSION: ")+v8::V8::GetVersion());
 std::unique_ptr<v8::ArrayBuffer::Allocator> allocator(v8::ArrayBuffer::Allocator::NewDefaultAllocator());
 post(i,"STAGE: allocator created");
 v8::Isolate::CreateParams params;params.array_buffer_allocator=allocator.get();
 params.oom_error_callback=oom;
 params.fatal_error_callback=[](const char* where,const char* msg){post(active_instance,std::string("ISOLATE FATAL: ")+where+" "+msg);};
 post(i,"STAGE: creating isolate");
 auto* isolate=v8::Isolate::New(params);
 post(i,"STAGE: isolate created");
 {
  v8::Isolate::Scope scope(isolate);v8::HandleScope handles(isolate);
  post(i,"STAGE: creating context");
  auto context=v8::Context::New(isolate);v8::Context::Scope context_scope(context);
  post(i,"STAGE: context created");
  v8::TryCatch caught(isolate);v8::Local<v8::String> source;v8::Local<v8::Script> script;v8::Local<v8::Value> result;
  post(i,"STAGE: creating source string");
  bool ok=v8::String::NewFromUtf8(isolate,text,v8::NewStringType::kNormal,len).ToLocal(&source);
  if(ok){post(i,"STAGE: compiling script");ok=v8::Script::Compile(context,source).ToLocal(&script);}
  if(ok){post(i,"STAGE: running script");ok=script->Run(context).ToLocal(&result);}
  post(i,"STAGE: script returned");
  if(ok){
   v8::String::Utf8Value value(isolate,result);post(i,std::string("RESULT: ")+(*value?*value:"<empty>"));
  }else{v8::String::Utf8Value err(isolate,caught.Exception());post(i,std::string("ERROR: ")+(*err?*err:"execution failed"));}
 }
 isolate->Dispose();
}
static PP_Bool create(PP_Instance,uint32_t,const char*[],const char*[]){return PP_TRUE;}
static void destroy(PP_Instance){}
static void view(PP_Instance,PP_Resource){}
static void focus(PP_Instance,PP_Bool){}
static PP_Bool document(PP_Instance,PP_Resource){return PP_FALSE;}
static PPP_Instance instance={create,destroy,view,focus,document};
static PPP_Messaging messages={message};
extern "C" int32_t PPP_InitializeModule(PP_Module,PPB_GetInterface get){vars=static_cast<const PPB_Var*>(get(PPB_VAR_INTERFACE));messaging=static_cast<const PPB_Messaging*>(get(PPB_MESSAGING_INTERFACE));return vars&&messaging?0:-1;}
extern "C" const void* PPP_GetInterface(const char* n){if(!std::strcmp(n,PPP_INSTANCE_INTERFACE))return &instance;if(!std::strcmp(n,PPP_MESSAGING_INTERFACE))return &messages;return nullptr;}
extern "C" void PPP_ShutdownModule(){}
