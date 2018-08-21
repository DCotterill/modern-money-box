from app import db
from app.forms import AddTransactionForm
from app.models import User, Account, Transaction
from flask import render_template
from flask_login import current_user, login_required
from app.main import bp


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    children = User.query.filter_by(parent_id=current_user.id).all()

    account_info = []
    for child in children:
        account_name = "No account"
        account_id = 0
        if len(child.accounts.all()) > 0:
            account_name = child.accounts[0].name
            account_id = child.accounts[0].id

        print("name:" + child.username + ",account:" + account_name, ",id"+str(account_id))
        account_info.append({"name": child.username, "account_name": account_name, "account_id": account_id})

    return render_template('index.html', title="Home", children=children, account_info=account_info)



@bp.route('/transactions/<account_id>', methods=['GET', 'POST'])
@login_required
def transactions(account_id):
    account = Account.query.filter_by(id=account_id).first_or_404()
    form = AddTransactionForm()

    print("account_id from URL:" + account_id)
    if form.validate_on_submit():
        print("account_id" + account_id)
        print("amount" + str(form.amount.data))
        print("description" + form.description.data)
        print("credit" + str(form.credit.data))
        print("debit" + str(form.debit.data))

        transaction = Transaction(account=account, description=form.description.data, amount=form.amount.data)
        db.session.add(transaction)
        db.session.commit()

    return render_template('transactions.html', account=account, form=form)