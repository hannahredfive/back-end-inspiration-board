from app import db

class Card(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    message= db.Column(db.String)
    likes_count= db.Column(db.Integer)

    board_id = db.Column(db.Integer, db.ForeignKey('board.board_id'))
    board = db.relationship("Board", back_populates="cards")

    def to_dict(self):
            card_dict = {
                "card_id" : self.card_id,
                "likes_count": self.likes_count,
                "message": self.message,
            }

            return card_dict

    @classmethod
    def from_dict(cls, card_data):
        return Card(likes_count=card_data["likes_count"],message=card_data["message"])