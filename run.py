# Imports
import streamlit as st
from streamlit import session_state as ss
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from streamlit_autorefresh import st_autorefresh
import numpy as np
import random
import ast
import app_functions as fx

import subprocess

if __name__ == '__main__':
    subprocess.run("streamlit run app.py")