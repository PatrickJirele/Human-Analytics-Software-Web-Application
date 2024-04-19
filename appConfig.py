# IMPORTS - START
import flask
import os
import re
from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime, date
from dateutil import relativedelta
import shutil
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
from flask_simple_crypt import SimpleCrypt
import squarify
import traceback
import matplotlib
from sqlalchemy import not_
import mpl_extra.treemap as tr # pip install git+https://github.com/chenyulue/matplotlib-extra


# IMPORTS - END

# CONFIG VARIABLES - START

OTHER_MIN_COUNT = 5		# What is the minimum quantity for something to be made into "other?"
OTHER_MIN_PERCENT = 2	# What is the minimum percent for something to be made into "other?"

# CONFIG VARIABLES - END