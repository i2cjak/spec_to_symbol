import logging
import os

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'debug.log')

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    filename=log_file,
    filemode='w' # Overwrite log on each run
)

logger = logging.getLogger(__name__)
