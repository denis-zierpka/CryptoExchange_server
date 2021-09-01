from datetime import datetime


class LastTimeOperation:
    def __init__(self) -> None:
        self.time = datetime.now()


class Info:
    default_user_money = '1000'
    Bitcoin_price = '200'
    Ethereum_price = '100'
    Litecoin_price = '80'
    Cardano_price = '10'
    Dogecoin_price = '150'

    failed = 'Failed\n'
    user_exists = 'Exists\n'
    register_success = 'User {} registered successfully\nYour id is: {}'
    login_success = 'User {} entered successfully\n'
    no_currency = 'You don\'t have any cryptocurrencies\n'
    not_enough_money = 'You don\'t have enough money for this operation\n'
    not_enough_cryptocurrency = (
        'You don\'t have enough cryptocurrency for this operation\n'
    )
    successful_operation = 'Successful! You balance of {} is {}\n'
    successful_added_new_currency = 'Successfully added {} currency\n'
    user_not_in_system = 'You are not in the system\n'
    done_message = 'Done\n'
    welcome_message = 'Welcome\n'
    rate_changed_during_operation = 'The currency rate changed during the operation'

    cryptocurrency_update_time = 10


time_of_last_operation = LastTimeOperation()
