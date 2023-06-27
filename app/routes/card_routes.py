from flask import Blueprint, request, jsonify, make_response, abort
from app import db
from app.models.board import Board
from app.models.card import Card
from .board_routes import validate_model
import os
import requests

# example_bp = Blueprint('example_bp', __name__)

cards_bp = Blueprint("cards_bp",__name__, url_prefix="/cards")


    
