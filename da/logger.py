import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('da')
# log_level = get_config_var('server.log_level', 'INFO')
# log_level = 'DEBUG'
# log_level = int(cache.config.get('main.log_level'))
# logger.setLevel(level="DEBUG")
# formatter = logging.Formatter(
#     '[%(asctime)s][%(name)s:%(lineno)d][%(levelname)s][%(process)d]: %(message)s')

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(pathname)s:%(lineno)d][%(levelname)s][%(process)d]: %(message)s',
                                                    datefmt='%Y-%m-%d %H:%M:%S'))
logger.setLevel(logging.DEBUG)
# console.setLevel(logging.DEBUG)
# console.setFormatter(formatter)
logger.addHandler(console)
