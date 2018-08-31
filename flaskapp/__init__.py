import os
import sys

from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

root_dir = os.getcwd()

# Load environment variables
load_dotenv(os.path.join(root_dir, '.env'))

# Add /flaskapp/analysis/ctpn to path to allow relative imports
ctpn_dir = os.path.join(root_dir, 'flaskapp', 'analysis', 'ctpn')
sys.path.append(ctpn_dir)

# Initialise tensorflow session
from flaskapp.analysis.ctpn.vision_ctpn import create_tf_session

tf_session = create_tf_session(
    config_filepath=os.path.join(ctpn_dir, 'text.yml'),
    model_filepath=os.path.join(ctpn_dir, 'ctpn.pb'))
app.config['tf_session'] = tf_session

# Import endpoints
from flaskapp import routes
