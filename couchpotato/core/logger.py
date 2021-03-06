import logging
import re


class CPLog(object):

    context = ''
    replace_private = ['api', 'apikey', 'api_key', 'password', 'username', 'h', 'uid', 'key', 'passkey']

    Env = None
    is_develop = False

    def __init__(self, context = ''):
        if context.endswith('.main'):
            context = context[:-5]

        self.context = context
        self.logger = logging.getLogger()

    def setup(self):

        if not self.Env:
            from couchpotato.environment import Env

            self.Env = Env
            self.is_develop = Env.get('dev')

            from couchpotato.core.event import addEvent
            addEvent('app.after_shutdown', self.close)

    def close(self, *args, **kwargs):
        logging.shutdown()

    def info(self, msg, replace_tuple = ()):
        self.logger.info(self.addContext(msg, replace_tuple))

    def info2(self, msg, replace_tuple = ()):
        self.logger.log(19, self.addContext(msg, replace_tuple))

    def debug(self, msg, replace_tuple = ()):
        self.logger.debug(self.addContext(msg, replace_tuple))

    def error(self, msg, replace_tuple = ()):
        self.logger.error(self.addContext(msg, replace_tuple))

    def warning(self, msg, replace_tuple = ()):
        self.logger.warning(self.addContext(msg, replace_tuple))

    def critical(self, msg, replace_tuple = ()):
        self.logger.critical(self.addContext(msg, replace_tuple), exc_info = 1)

    def addContext(self, msg, replace_tuple = ()):
        return '[%+25.25s] %s' % (self.context[-25:], self.safeMessage(msg, replace_tuple))

    def safeMessage(self, msg, replace_tuple = ()):

        from couchpotato.core.helpers.encoding import ss, toUnicode

        msg = ss(msg)

        try:
            if isinstance(replace_tuple, tuple):
                msg = msg % tuple([ss(x) if not isinstance(x, (int, float)) else x for x in list(replace_tuple)])
            elif isinstance(replace_tuple, dict):
                msg = msg % dict((k, ss(v)) for k, v in replace_tuple.iteritems())
            else:
                msg = msg % ss(replace_tuple)
        except Exception as e:
            self.logger.error('Failed encoding stuff to log "%s": %s' % (msg, e))

        self.setup()
        if not self.is_develop:

            for replace in self.replace_private:
                msg = re.sub('(\?%s=)[^\&]+' % replace, '?%s=xxx' % replace, msg)
                msg = re.sub('(&%s=)[^\&]+' % replace, '&%s=xxx' % replace, msg)

            # Replace api key
            try:
                api_key = self.Env.setting('api_key')
                if api_key:
                    msg = msg.replace(api_key, 'API_KEY')
            except:
                pass

        return toUnicode(msg)
