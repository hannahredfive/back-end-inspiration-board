from flask import Blueprint, request, jsonify, make_response, abort
from app import db
from app.models.board import Board
from app.models.card import Card
import os
import requests

# example_bp = Blueprint('example_bp', __name__)

boards_bp = Blueprint("boards_bp",__name__, url_prefix="/boards")

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"message":f"{cls.__name__} {model_id} invalid"}, 400))

    model = cls.query.get(model_id)

    if not model:
        abort(make_response({"message":f"{cls.__name__} {model_id} not found"}, 404))

    return model


@boards_bp.route("", methods=["GET"])
def read_all_boards():

    boards = Board.query.all()

    boards_response = []
    for board in boards:
        boards_response.append(board.to_dict())

    return jsonify(boards_response), 200

@boards_bp.route("/<board_id>", methods=["GET"])
def read_one_board(board_id):
    board = validate_model(Board, board_id)

    return make_response({"boards": board.to_dict()})

    def post_to_slack(message):
        url = 'https://slack.com/api/chat.postMessage'
        payload = {
                'token': os.environ.get("SLACK_API_TOKEN"),
                'channel': '#inspogroup-fluffybutt',
                'text': message
            }
        response = requests.post(url, data=payload)
        return_response = response.status_code
        db.session.commit()

    return jsonify({"board": board.to_dict()}), 200

@boards_bp.route("", methods=["POST"])
def create_board():
    request_body = request.get_json()

    try:
        new_board = Board.from_dict(request_body)
    except:
        return {"details": "Invalid data"} , 400
    
    db.session.add(new_board)
    db.session.commit()

    return make_response({"boards": new_board.to_dict()}, 201)


@boards_bp.route("", methods=["DELETE"])
def delete_all_boards():
    boards = Board.query.all()
    for board in boards:
        db.session.delete(board)
    db.session.commit()

    return make_response({"details": f"Boards successfully deleted"}, 200)


@boards_bp.route("/<board_id>", methods=["DELETE"])
def delete_board(board_id):
    board = validate_model(Board, board_id)

    db.session.delete(board)
    db.session.commit()

    return abort(make_response({"details":f"Board {board_id} \"{board.title}\" successfully deleted"}, 200))


@boards_bp.route("/<board_id>/cards", methods=["POST"])
def post_cards_under_board(board_id):
    board = validate_model(Board, board_id)
    request_body = request.get_json()
    card_details = request_body["message"]

    card = Card(board_id=board.board_id, likes_count=0, message=card_details)

    db.session.add(card)
    db.session.commit()

    return make_response({"board_id": board.board_id, "cards": card.to_dict()}, 201)

