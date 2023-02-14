import csv
import random
from collections import defaultdict
from email.utils import parseaddr
from typing import Any, Dict, List


DONATION_INDEX = 1
EMAIL_INDEX = 3
NAME_INDEX = 4
PRINT_ENTRIES = False
SELECT_WINNER = True
CSV_FILE_NAME = 'tiltify.csv'


class Entrant():

    def __init__(self, email: str, name: str):
        self.__email: str = email
        self.__name: str = name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Entrant):
            return self.__email == other.getEmail()
        else:
            return False

    def getEmail(self) -> str:
        return self.__email

    def getName(self) -> str:
        return self.__name

    def __hash__(self) -> int:
        return hash(self.__email)

    def __str__(self) -> str:
        return self.__email


# Create a dictionary of entrant emails to prevent potential issues where
# people could donate more than once that would otherwise allow them to bypass
# the $50 threshold

emailToEntrant: Dict[str, Entrant] = dict()
entrantToDonationDollarAmount: Dict[Entrant, int] = defaultdict(lambda: 0)

with open(CSV_FILE_NAME, newline = '') as csvFile:
    csvFileReader = csv.reader(csvFile, delimiter = ',')

    for csvRow in csvFileReader:
        email = csvRow[EMAIL_INDEX].strip().lower()

        parsedEmail = parseaddr(email)
        if parsedEmail is None or not isinstance(parsedEmail[0], str) or not isinstance(parsedEmail[1], str) or len(parsedEmail[1]) == 0:
            raise ValueError(parsedEmail)

        if email not in emailToEntrant:
            name = csvRow[NAME_INDEX].strip()
            emailToEntrant[email] = Entrant(
                email = email,
                name = name
            )

        entrant = emailToEntrant[email]

        donationAmountStr = csvRow[DONATION_INDEX]

        try:
            donationAmountFloat = float(donationAmountStr)
        except ValueError as e:
            print(f'Encountered exception when trying to convert donationAmountStr to float: \"{donationAmountStr}\"')
            raise e

        # Round the donation amount to the nearest whole dollar
        donationAmountInt = int(round(donationAmountFloat))

        entrantToDonationDollarAmount[entrant] = entrantToDonationDollarAmount[entrant] + donationAmountInt


# Determine the exact number of entries that each entrant has

entrantToEntriesAmount: Dict[Entrant, int] = dict()

for entrant, donationAmount in entrantToDonationDollarAmount.items():
    entries: int = 0

    if donationAmount <= 50:
        entries = donationAmount
    else:
        entries = ((donationAmount - 50) // 2) + 50

    entrantToEntriesAmount[entrant] = entries


# At this point, we now have the list of entrants, and also their exact number
# of entries

if PRINT_ENTRIES:
    totalRaised = 0
    for entrant in emailToEntrant.values():
        print(f'entrant={entrant.getName()}, dollarAmount={entrantToDonationDollarAmount[entrant]}, entriesAmount={entrantToEntriesAmount[entrant]}')
        totalRaised = totalRaised + entrantToDonationDollarAmount[entrant]
    print(f'Total raised: {totalRaised}')

weightedEntries: List[str] = list()

for entrant, entriesAmount in entrantToEntriesAmount.items():
    for _ in range(entriesAmount):
        weightedEntries.append(entrant.getEmail())

if SELECT_WINNER:
    winnerEmail = random.choice(weightedEntries)
    winner = emailToEntrant[winnerEmail]

    print(f'\n################\n################')

    if winner.getName() is None or len(winner.getName()) == 0 or winner.getName().isspace():
        print(f'THE WINNER IS: {winner.getEmail()}')
    else:
        print(f'THE WINNER IS: {winner.getName()}')

    print(f'################\n################\n')
