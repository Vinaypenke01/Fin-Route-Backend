"""
guest_workspace/services/calculator_service.py

CalculatorService provides stateless loan calculations (`app.calculator.tsx`).
Calculates schedules, installment amounts (EMI), total interest, and total payable.
"""

from datetime import date, timedelta


class CalculatorService:
    """
    Stateless loan calculation engine. No database access.
    """

    @staticmethod
    def calculate_loan(
        amount: float,
        interest_rate: float,
        interest_type: str,  # 'flat_percentage', 'fixed_amount', 'monthly_percentage'
        frequency: str,      # 'daily', 'weekly', 'monthly'
        duration: int,        # Number of installments
        start_date: date = None,
    ) -> dict:
        """
        Calculate installment breakdown and return complete repayment schedule.
        """
        if start_date is None:
            start_date = date.today()

        amount = float(amount)
        interest_rate = float(interest_rate)

        # 1. Total Interest Calculation
        if interest_type == "flat_percentage":
            total_interest = round(amount * (interest_rate / 100), 2)
        elif interest_type == "fixed_amount":
            total_interest = round(interest_rate, 2)
        elif interest_type == "monthly_percentage":
            # Assuming duration is in months or installments
            total_interest = round(amount * (interest_rate / 100) * (duration / 30 if frequency == "daily" else duration), 2)
        else:
            total_interest = round(amount * (interest_rate / 100), 2)

        total_payable = round(amount + total_interest, 2)
        installment_amount = round(total_payable / max(1, duration), 2)

        # 2. Schedule Generation
        schedule = []
        current_date = start_date
        remaining_balance = total_payable

        for i in range(1, duration + 1):
            if frequency == "daily":
                current_date += timedelta(days=1)
            elif frequency == "weekly":
                current_date += timedelta(weeks=1)
            elif frequency == "monthly":
                # Add ~30 days
                current_date += timedelta(days=30)

            # Adjust final installment for rounding diffs
            if i == duration:
                due_amount = remaining_balance
                remaining_balance = 0.0
            else:
                due_amount = min(installment_amount, remaining_balance)
                remaining_balance = round(remaining_balance - due_amount, 2)

            schedule.append({
                "installment_number": i,
                "due_date": current_date.isoformat(),
                "installment_amount": round(due_amount, 2),
                "remaining_balance": max(0.0, remaining_balance),
            })

        return {
            "principal_amount": amount,
            "interest_rate": interest_rate,
            "interest_type": interest_type,
            "total_interest": total_interest,
            "total_payable": total_payable,
            "installment_amount": installment_amount,
            "frequency": frequency,
            "duration": duration,
            "schedule": schedule,
        }
