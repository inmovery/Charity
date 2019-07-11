from ThreadManager import ThreadManager


class DataPerson:

    def __init__(self, mRejectionReason, mPatientName, mRegion, mAge, mDiagnosis, mTgsk, mDisability, mDrugs, mEmail, mMobile, mHelpWithDrugs, mAppealHospital, mHoldMedicalCommission, mMinistryHealth, mProsecutor, mCourtAppeal, mRepresentativeName,
                 mStepRejectionReason, mStepPatientName, mStepRepresentativeName, mStepRegion, mStepAge, mStepDiagnosis, mStepTgsk, mStepDisability, mStepDrugs, mStepEmail, mStepMobile, mStepHelpWithDrugs, mStepAppealHospital, mStepHoldMedicalCommission,
                 mStepMinistryHealth, mStepProsecutor, mStepCourtAppeal, mStepForCheckNeed, mStepForQuestions, mStepForMobile, mStepForEmail, mStepForDisability, mStepForTgsk, mStepForDiagnosis, mStepCheckRepresentativeName, mStepForRepresentativeName, mUserId):

        self.tm = ThreadManager(mUserId)

        # основные поля пользователя
        self.rejection_reason = mRejectionReason
        self.patient_name = mPatientName
        self.representative_name = mRepresentativeName
        self.region = mRegion
        self.age = mAge
        self.diagnosis = mDiagnosis
        self.tgsk = mTgsk
        self.disability = mDisability
        self.drugs = mDrugs
        self.email = mEmail
        self.mobile = mMobile
        self.help_with_drugs = mHelpWithDrugs

        # проверка законного представителя
        self.stepCheckRepresentativeName = mStepCheckRepresentativeName

        # отслежвание передвижений пользователей по дефолтным вопросам
        self.stepRejectionReason = mStepRejectionReason
        self.stepPatientName = mStepPatientName
        self.stepRepresentativeName = mStepRepresentativeName
        self.stepRegion = mStepRegion
        self.stepAge = mStepAge
        self.stepDiagnosis = mStepDiagnosis
        self.stepTgsk = mStepTgsk
        self.stepDisability = mStepDisability
        self.stepDrugs = mStepDrugs
        self.stepEmail = mStepEmail
        self.stepMobile = mStepMobile
        self.stepHelpWithDrugs = mStepHelpWithDrugs

        # вопросы по обращениям
        self.appeal_hospital = mAppealHospital
        self.hold_medical_commission = mHoldMedicalCommission
        self.ministry_health = mMinistryHealth
        self.prosecutor = mProsecutor
        self.court_appeal = mCourtAppeal

        self.stepAppealHospital = mStepAppealHospital
        self.stepHoldMedicalCommission = mStepHoldMedicalCommission
        self.stepMinistryHealth = mStepMinistryHealth
        self.stepProsecutor = mStepProsecutor
        self.stepCourtAppeal = mStepCourtAppeal

        self.stepForCheckNeed = mStepForCheckNeed
        self.stepForQuestions = mStepForQuestions
        self.stepForMobile = mStepForMobile
        self.stepForEmail = mStepForEmail
        self.stepForDisability = mStepForDisability
        self.stepForTgsk = mStepForTgsk
        self.stepForDiagnosis = mStepForDiagnosis

        self.stepForRepresentativeName = mStepForRepresentativeName