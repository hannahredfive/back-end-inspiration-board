from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.board import Board

# example_bp = Blueprint('example_bp', __name__)

boards_bp = Blueprint("boards_bp",__name__, url_prefix="/boards")

@boards_bp.route("",methods=["GET"])
def read_all_boards():

    boards = Board.query.all()

    boards_response = []
    for board in boards:
        boards_response.append(board.to_dict())

    return jsonify(boards_response), 200