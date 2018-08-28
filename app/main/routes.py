from app import db
from app.forms import AddTransactionForm
from app.models import User, Account, Transaction, load_user, TransactionType
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.main import bp
import csv
from io import StringIO
import decimal


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    user = load_user(current_user.id)
    if user.is_parent_user:
        children = User.query.filter_by(parent_id=current_user.id).all()

        account_info = []
        for child in children:
            account_name = "No account"
            account_id = 0
            if len(child.accounts.all()) > 0:
                account_name = child.accounts[0].name
                account_id = child.accounts[0].id
                account_balance = child.accounts[0].balance

            account_info.append({"name": child.username, "account_balance": account_balance,
                                 "account_name": account_name, "account_id": account_id})

    else:
        account_info = []
        account_name = "No account"
        account_id = 0
        if len(user.accounts.all()) > 0:
            account_name = user.accounts[0].name
            account_id = user.accounts[0].id
            account_balance = user.accounts[0].balance

        account_info.append({"name": user.username, "account_balance": account_balance,
                             "account_name": account_name, "account_id": account_id})

    return render_template('index.html', title="Home", account_info=account_info)


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

        if form.credit.data:
            transaction.type = TransactionType.CREDIT.value
            account.balance = account.balance + decimal.Decimal(form.amount.data)
        else:
            transaction.type = TransactionType.DEBIT.value
            account.balance = account.balance - decimal.Decimal(form.amount.data)

        db.session.add(transaction)
        db.session.commit()

    return render_template('transactions.html', account=account, form=form)


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            content = file.read()
            content = content.decode('utf-8')
            print(content)
            csv_reader = csv.reader(StringIO(content), delimiter=',')

            user = load_user(current_user.id)
            current_account = user.accounts[0]

            for row in csv_reader:

                balance = 0

                transaction_date = row[0]
                description = row[1]
                credit = row[2]
                debit = row[3]

                transaction = Transaction(created_date=transaction_date, description=description,
                                          account=current_account)
                if credit:
                    transaction.type = TransactionType.CREDIT.value
                    transaction.amount = credit
                    current_account.balance = current_account.balance + decimal.Decimal(credit)
                else:
                    transaction.type = TransactionType.DEBIT.value
                    transaction.amount = debit
                    current_account.balance = current_account.balance - decimal.Decimal(debit)

                print(transaction)
                db.session.add(transaction)

            print(current_account.balance)
            db.session.commit()

            return redirect(url_for('main.index'))
    return render_template('upload_transactions.html')
