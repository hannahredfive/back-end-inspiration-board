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

    text_str = "Someone just created a card in " + board.board_id 

    card = Card(board_id=board.board_id, likes_count=0, message=card_details)

    url = 'https://slack.com/api/chat.postMessage'
    payload = {
            'token': os.environ.get("SLACK_API_TOKEN"),
            'channel': '#inspogroup-fluffybutt',
            'text': text_str
        }
    # header_key = os.environ.get("authorization")

    response = requests.post(url=url, json=payload)
    return_response = response.status_code


    db.session.add(card)
    db.session.commit()

    return make_response({"board_id": board.board_id, "cards": card.to_dict()}, 201)


@boards_bp.route("/<board_id>/cards", methods=["GET"])
def get_card_under_board(board_id):
    board = validate_model(Board, board_id)
    cards = Card.query.filter_by(board_id=board.board_id).all()
    card_list = [card.to_dict() for card in cards]

    return make_response({"board_id": board.board_id, "cards": card_list}, 200)


@boards_bp.route("/<board_id>/cards", methods=["DELETE"])
def delete_all_cards_from_board(board_id):
    board = validate_model(Board, board_id)
    cards = Card.query.filter_by(board_id=board.board_id).all()

    if not cards:
        return make_response("No cards found", 404)
    else:
        for card in cards:
            db.session.delete(card)
        db.session.commit()

        return make_response(f"All cards from board {board_id} have been deleted", 200)
    

@boards_bp.route("/<board_id>/cards/<card_id>", methods=["DELETE"])
def delete_card(board_id, card_id):
    board = validate_model(Board, board_id)

    if board is None:
        return make_response(jsonify({"error": "Board not found"}), 404)
    
    card = validate_model(Card, card_id)

    if card not in board.cards:
        return make_response(jsonify({"error": "Card not found in this board"}), 404)
    
    db.session.delete(card)
    db.session.commit()

    return make_response(jsonify({"details": f"Card {card_id} \"{card.message}\" successfully deleted"}, 200))


@boards_bp.route("/<board_id>/cards/<card_id>", methods=["PATCH"])
def update_increment_likes_in_card(board_id, card_id):
    card = validate_model(Card, card_id)

    if card is None:
        return make_response(jsonify({"error": "Card not found"}), 400)
    
    card.likes_count += 1

    db.session.commit()

    return make_response(jsonify({"card": card.to_dict()}), 200)



@boards_bp.route("/<board_id>/cards/<card_id>", methods=["PUT"])
def update_decrement_likes_in_card(board_id, card_id):
    card = validate_model(Card, card_id)

    if card is None:
        return make_response(jsonify({"error": "Card not found"}), 400)
    
    card.likes_count -= 1

    db.session.commit()

    return make_response(jsonify({"card": card.to_dict()}), 200)
