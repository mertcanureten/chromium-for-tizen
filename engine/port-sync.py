"""NaCl lacks sem_timedwait: bounded 1 ms polling fallback for experimental V8."""
from pathlib import Path
p=Path('/work/v8/src/base/platform/semaphore.cc');s=p.read_text()
old='''bool Semaphore::WaitFor(const TimeDelta& rel_time) {
  // Compute the time for end of timeout.'''
new='''bool Semaphore::WaitFor(const TimeDelta& rel_time) {
#if defined(V8_OS_NACL)
  const auto deadline = TimeTicks::Now() + rel_time;
  for (;;) {
    if (sem_trywait(&native_handle_) == 0) return true;
    CHECK(errno == EAGAIN || errno == EINTR);
    auto remaining = deadline - TimeTicks::Now();
    if (remaining.InMicroseconds() <= 0) return false;
    usleep(static_cast<useconds_t>(std::min<int64_t>(1000, remaining.InMicroseconds())));
  }
#else
  // Compute the time for end of timeout.'''
if new not in s:
 assert old in s;s=s.replace(old,new)
 s=s.replace('\n#elif V8_OS_WIN\n\nSemaphore::Semaphore', '\n#elif V8_OS_WIN\n\nSemaphore::Semaphore')
 end='''    DCHECK_EQ(EINTR, errno);
  }
}

#elif V8_OS_WIN'''
 assert end in s;s=s.replace(end,'''    DCHECK_EQ(EINTR, errno);
  }
#endif
}

#elif V8_OS_WIN''')
 s=s.replace('#include <errno.h>','#include <errno.h>\n#if defined(V8_OS_NACL)\n#include <unistd.h>\n#include <algorithm>\n#endif')
 p.write_text(s)
