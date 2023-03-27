
def sign_loan(loan):
    loan.borrower_signature = "adsf"
    loan.lender_signature = "asdf"
    return loan

def create_payment_schedule(loan, interest_rate, total_duration):
    print(loan)
