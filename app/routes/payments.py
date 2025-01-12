# app/routes/payments.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Visit, Payment, db

bp = Blueprint('payments', __name__, url_prefix='/payments')


@bp.route('/deposit', methods=['POST'])
@jwt_required()
def make_deposit():
    data = request.get_json()
    visit_id = data['visit_id']
    visit = Visit.query.get_or_404(visit_id)

    # Implement Bkash integration here
    # Handle payment processing
    payment = Payment(
        visit_id=visit_id,
        amount=data['amount'],
        payment_method='bkash',
        bkash_number=data['bkash_number'],
        transaction_id=data['transaction_id'],
        status='completed'
    )

    db.session.add(payment)
    visit.payment_status = 'deposit_paid'
    db.session.commit()

    return jsonify({'message': 'Deposit payment successful'})


@bp.route('/refund', methods=['POST'])
@jwt_required()
def process_refund():
    data = request.get_json()
    visit_id = data['visit_id']
    visit = Visit.query.get_or_404(visit_id)

    # Implement refund logic here
    # Handle Bkash refund processing

    refund = Payment(
        visit_id=visit_id,
        amount=-data['amount'],  # Negative amount for refund
        payment_method='bkash',
        bkash_number=data['bkash_number'],
        transaction_id=data['refund_transaction_id'],
        status='refunded'
    )

    db.session.add(refund)
    visit.payment_status = 'refunded'
    db.session.commit()

    return jsonify({'message': 'Refund processed successfully'})