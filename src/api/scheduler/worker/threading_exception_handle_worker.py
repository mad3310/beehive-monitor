import threading
import logging
import traceback

from tornado.options import options
from utils.mail import send_email
from tornado.web import HTTPError
from utils.exceptions import HTTPAPIError
from utils.threading_exception_queue import Threading_Exception_Queue
from utils import getHostIp
from utils.invokeCommand import InvokeCommand


class Thread_Exception_Handler_Worker(threading.Thread):
    
    threading_exception_queue = Threading_Exception_Queue()
    
    def __init__(self):
        super(Thread_Exception_Handler_Worker,self).__init__()
    
    def run(self):
        exc_info = None
        try:
            while not self.threading_exception_queue.empty():
                exc_info = self.threading_exception_queue.get(block=False)
                logging.info('get exc_info: %s' % str(exc_info))
                if exc_info is None:
                    continue
                
                e = exc_info[1]
    
                if isinstance(e, HTTPAPIError):
                    pass
                elif isinstance(e, HTTPError):
                    e = HTTPAPIError(e.status_code)
                else:
                    e = HTTPAPIError(500)
    
                exception = "".join([ln for ln in traceback.format_exception(*exc_info)])
    
                logging.error(e)
                self._send_error_email(exception)
        except:
            logging.error('exc_info : %s' % str( exc_info) )
            exc_type, exc_obj, exc_trace = exc_info
            # deal with the exception
            logging.error(exc_type)
            logging.error(exc_obj)
            logging.error(exc_trace)
            self._send_error_email(exc_type+exc_obj+exc_trace)
            
    def _send_error_email(self, exception):
        try:
            # send email
            host_ip = getHostIp()
            invokeCommand = InvokeCommand()
            cmd_str = "rpm -qa container-manager"
            version_str = invokeCommand._runSysCmd(cmd_str)
            subject = "[%s]Internal Server Error" % options.sitename
            
            exception += "\n" + version_str[0] + "\nhost ip :" + host_ip
            
#            body = self.render_string("errors/500_email.html", exception=exception)
            
#            email_from = "%s <noreply@%s>" % (options.sitename, options.domain)
            if options.send_email_switch:
                send_email(options.admins, subject, exception)
        except Exception:
            logging.error(traceback.format_exc())


