from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from .models import User, Group, GroupMember, Expense, db
from .business_logic import calculate_split
import bcrypt
import datetime

bp = Blueprint('api', __name__)

@bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    password_hash = hash_password(data['password'])
    new_user = User(name=data['name'], email=data['email'], password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id' : new_user.id}), 201

@bp.route('/users/<int:user_id', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 200

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@bp.route('/groups/<int:group_id>/members', methods=['POST'])
def add_group_member(group_id):
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    new_member = GroupMember(group_id=group_id, user_id=user.id)
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'id' : new_member.id}), 201

@bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expenses():
    data = request.json
    new_expense = Expense(
        user_id=data['user_id'],
        group_id=data['group_id'],
        amount=data['amount'],
        description=data['description']
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'id': new_expense.id}), 201

@bp.route('/groups/<int:group_id>/balance', methods=['GET'])
def get_group_balance(group_id):
    balances = calculate_split(group_id)
    return jsonify(balances)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(user_input_password, hashed_password):
    return bcrypt.checkpw(user_input_password.encode('utf-8'), hashed_password)

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and verify_password(data['password'], user.password):
        access_token = create_access_token(
            identity=user.id,
            expires_delta=datetime.timedelta(days=1)
        )
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    new_group = Group(group_name=data['group_name'])
    db.session.add(new_group)
    db.session.commit()
    return jsonify({'id': new_group.id}), 201

@bp.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    return jsonify({'id': group.id, 'group_name': group.group_name}), 200

@bp.route('/groups', methods=['GET'])
def list_groups():
    groups = Group.query.all()
    return jsonify([{'id': group.id, 'group_name': group.group_name} for group in groups]), 200

@bp.route('/expenses/<int:expense_id', methods=['GET'])
def get_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    return jsonify({
        'id': expense.id,
        'user_id': expense.user_id,
        'group_id': expense.group_id,
        'amount': expense.amount,
        'description': expense.description,
        'date': expense.date
    }), 200

@bp.route('/groups/<int:group_id>/expenses', methods=['GET'])
@jwt_required()
def list_group_expenses(group_id):
    expenses = Expense.query.filter_by(group_id=group_id).all()
    return jsonify([
        {
            'id': exp.id,
            'user_id': exp.user_id,
            'group_id': exp.group_id,
            'amount': exp.amount,
            'description': exp.description,
            'date': exp.date
        } for exp in expenses
    ]), 200

@bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    data = request.json
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    expense.amount = data.get('amount', expense.amount)
    expense.description = data.get('description', expense.description)
    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'}), 200

@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'}), 200
