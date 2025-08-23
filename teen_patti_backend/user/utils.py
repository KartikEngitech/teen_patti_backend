from game.models import UserWallet
import uuid
import random
import string
from decimal import Decimal


# def reward_referral_chain(user):
#     # Rewards from level 0 (direct referrer) up to level 5
#     rewards = [
#         Decimal('50.00'),
#         Decimal('30.00'),
#         Decimal('20.00'),
#         Decimal('15.00'),
#         Decimal('5.00'),
#         Decimal('5.00')
#     ]

#     current_user = user.referred_by
#     level = 0

#     print(f"\n--- Referral Reward Distribution Started for: {user.email} ---")

#     while current_user and level < len(rewards):
#         reward_amount = rewards[level]
#         wallet, _ = UserWallet.objects.get_or_create(user=current_user)

#         # Ensure balance is Decimal
#         if not isinstance(wallet.balance, Decimal):
#             wallet.balance = Decimal(wallet.balance)

#         wallet.balance += reward_amount
#         wallet.save()

#         print(f"Level {level + 1}: {current_user.email} received ₹{reward_amount}. New Balance: ₹{wallet.balance}")

#         current_user = current_user.referred_by
#         level += 1

#     print(f"--- Referral Reward Distribution Completed for: {user.email} ---\n")




def reward_referral_chain(user, base_reward_amount):
    reward_percentages = [100, 50, 30, 20, 5, 5, 5]

    current_user = user.referred_by
    level = 0

    print(f"\n--- Referral Reward Distribution Started for: {user.email} ---")

    while current_user and level < len(reward_percentages):
        percentage = reward_percentages[level]
        reward_amount = (Decimal(percentage) / Decimal(100)) * base_reward_amount

        wallet, _ = UserWallet.objects.get_or_create(user=current_user)

        if not isinstance(wallet.balance, Decimal):
            wallet.balance = Decimal(wallet.balance)

        wallet.balance += reward_amount
        wallet.save()

        print(f"Level {level + 1}: {current_user.email} received ₹{reward_amount} ({percentage}%). New Balance: ₹{wallet.balance}")

        current_user = current_user.referred_by
        level += 1

    print(f"--- Referral Reward Distribution Completed for: {user.email} ---\n")


def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
