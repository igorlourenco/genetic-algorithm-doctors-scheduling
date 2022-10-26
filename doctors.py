from enum import Enum

import numpy as np


class WeekDays (Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class DoctorSchedulingProblem:
    def __init__(self, hardConstraintPenalty):

        # penalty factor for each hard constraint violation:
        self.hardConstraintPenalty = hardConstraintPenalty

        # list of doctors:
        self.doctors = ['João', 'Marina', 'Cássio',
                        'Tiana', 'Éder', 'Fabio', 'Guida', 'Alice']

        # doctors' respective shift preferences - morning, evening, night:
        self.shiftPreference = [[1, 0, 0], [1, 1, 0], [0, 0, 1], [
            0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 1, 1], [1, 1, 1]]

        # min and max number of doctors allowed for each shift - morning, evening, night:
        self.shiftMin = [2, 2, 1]
        self.shiftMax = [3, 3, 2]

        # max shifts per week allowed for each doctor
        self.maxShiftsPerWeek = 5

        # number of weeks we create a schedule for:
        self.weeks = 1

        # useful values:
        self.shiftPerDay = len(self.shiftMin)
        self.shiftsPerWeek = 7 * self.shiftPerDay

    # return the number of shifts in the schedule
    def __len__(self):
        return len(self.doctors) * self.shiftsPerWeek * self.weeks

    # get fitness score for the given schedule:
    def getCost(self, schedule):
        if len(schedule) != self.__len__():
            raise ValueError(
                "size of schedule list should be equal to ", self.__len__())

        # convert entire schedule into a dictionary with a separate schedule for each doctor:
        doctorShiftsDict = self.getDoctorShifts(schedule)

        # count the various violations:

        # hard
        consecutiveShiftViolations = self.countConsecutiveShiftViolations(
            doctorShiftsDict)
        shiftsPerWeekViolations = self.countShiftsPerWeekViolations(doctorShiftsDict)[
            1]
        doctorsPerShiftViolations = self.countDoctorsPerShiftViolations(doctorShiftsDict)[
            1]

        # soft
        shiftPreferenceViolations = self.countShiftPreferenceViolations(
            doctorShiftsDict)

        # calculate the cost of the violations:
        hardConstraintViolations = consecutiveShiftViolations +\
            doctorsPerShiftViolations + shiftsPerWeekViolations
        softConstraintViolations = shiftPreferenceViolations

        return self.hardConstraintPenalty * hardConstraintViolations + softConstraintViolations  # 101

    def getDoctorShifts(self, schedule):
        """
        Converts the entire schedule into a dictionary with a separate schedule for each doctor
        :param schedule: a list of binary values describing the given schedule
        :return: a dictionary with each doctor as a key and the corresponding shifts as the value
        """
        shiftsPerDoctor = self.__len__() // len(self.doctors)
        doctorShiftsDict = {}
        shiftIndex = 0

        for doctor in self.doctors:
            doctorShiftsDict[doctor] = schedule[shiftIndex:shiftIndex + shiftsPerDoctor]
            shiftIndex += shiftsPerDoctor

        return doctorShiftsDict

    # counts the consecutive shift violations in the schedule
    def countConsecutiveShiftViolations(self, doctorShiftsDict):
        violations = 0
        # iterate over the shifts of each doctor:
        for doctorShifts in doctorShiftsDict.values():
            # look for two consecutive '1's:
            for shift1, shift2 in zip(doctorShifts, doctorShifts[1:]):
                if shift1 == 1 and shift2 == 1:
                    violations += 1
        return violations

    # counts the max-shifts-per-week violations in the schedule
    def countShiftsPerWeekViolations(self, doctorShiftsDict):
        violations = 0
        weeklyShiftsList = []
        # iterate over the shifts of each doctor:
        for doctorShifts in doctorShiftsDict.values():  # all shifts of a single doctor
            # iterate over the shifts of each weeks:
            for i in range(0, self.weeks * self.shiftsPerWeek, self.shiftsPerWeek):
                # count all the '1's over the week:
                weeklyShifts = sum(doctorShifts[i:i + self.shiftsPerWeek])
                weeklyShiftsList.append(weeklyShifts)
                if weeklyShifts > self.maxShiftsPerWeek:
                    violations += weeklyShifts - self.maxShiftsPerWeek

        return weeklyShiftsList, violations

        # counts the number-of-doctors-per-shift violations in the schedule
    def countDoctorsPerShiftViolations(self, doctorShiftsDict):
        # sum the shifts over all doctors:
        totalPerShiftList = [sum(shift)
                             for shift in zip(*doctorShiftsDict.values())]

        violations = 0
        # iterate over all shifts and count violations:
        for shiftIndex, numOfDoctors in enumerate(totalPerShiftList):
            # -> 0, 1, or 2 for the 3 shifts per day
            dailyShiftIndex = shiftIndex % self.shiftPerDay
            if (numOfDoctors > self.shiftMax[dailyShiftIndex]):
                violations += numOfDoctors - self.shiftMax[dailyShiftIndex]
            elif (numOfDoctors < self.shiftMin[dailyShiftIndex]):
                violations += self.shiftMin[dailyShiftIndex] - numOfDoctors

        return totalPerShiftList, violations

        # counts the doctor-preferences violations in the schedule
    def countShiftPreferenceViolations(self, doctorShiftsDict):
        violations = 0
        for doctorIndex, shiftPreference in enumerate(self.shiftPreference):
            # duplicate the shift-preference over the days of the period
            preference = shiftPreference * \
                (self.shiftsPerWeek // self.shiftPerDay)
            # iterate over the shifts and compare to preferences:
            shifts = doctorShiftsDict[self.doctors[doctorIndex]]
            for pref, shift in zip(preference, shifts):
                if pref == 0 and shift == 1:
                    violations += 1

        return violations

        # prints the schedule and violations details
    def printScheduleInfo(self, schedule):
        doctorShiftsDict = self.getDoctorShifts(schedule)

        print("Schedule for each doctor:")
        for doctor in doctorShiftsDict:  # all shifts of a single doctor
            print(doctor, ":")
            days = np.array_split(doctorShiftsDict[doctor], 7)
            index = 0
            for day in days:
                print(WeekDays(index).name, day)
                index += 1

            print('\n\n')

        weeklyShiftsList, violations = self.countShiftsPerWeekViolations(
            doctorShiftsDict)
        print("weekly Shifts = ")
        index = 0
        for weeklyShifts in weeklyShiftsList:
            print(self.doctors[index], weeklyShifts)
            index += 1

        print('\n\n')
        print("Shifts Per Week Violations = ", violations)
        print()

        print("consecutive shift violations = ",
              self.countConsecutiveShiftViolations(doctorShiftsDict))
        print()

        totalPerShiftList, violations = self.countDoctorsPerShiftViolations(
            doctorShiftsDict)
        print("Doctors Per Shift = ", totalPerShiftList)
        print("Doctors Per Shift Violations = ", violations)
        print()

        shiftPreferenceViolations = self.countShiftPreferenceViolations(
            doctorShiftsDict)
        print("Shift Preference Violations = ", shiftPreferenceViolations)
        print()


# testing the class:
def main():
    # create a problem instance:
    doctors = DoctorSchedulingProblem(10)

    randomSolution = np.random.randint(2, size=len(doctors))
    print("Random Solution = ")
    print(randomSolution)
    print()

    doctors.printScheduleInfo(randomSolution)

    print("Total Cost = ", doctors.getCost(randomSolution))


if __name__ == "__main__":
    main()


# [1 1 1 0 1 0 1 0 0 1] = 718
