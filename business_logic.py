from .models import Expense, GroupMember, db

def calculate_split(group_id):
    expenses = Expense.query.filter_by(group_id=group_id).all()
    members= GroupMember.query.filter_by(group_id=group_id).all()

    total_amount = sum(exp.amount for exp in expenses)
    per_person = total_amount / len(members)

    balances = {}
    for member in members:
        balances[member.user_id] = per_person

    for expense in expenses:
        balances[expense.user_id] -= expense.amount

    return balances