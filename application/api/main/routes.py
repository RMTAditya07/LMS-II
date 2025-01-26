from flask import Blueprint, render_template, send_from_directory, current_app

from . import main_bp

@main_bp.route('/')
def home():
    return render_template('index.html')