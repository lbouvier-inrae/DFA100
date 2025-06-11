#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: settings_manager.py
Author: Maxime Gosselin
Contact: maximeg391@gmail.com
License: MIT License
"""
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
