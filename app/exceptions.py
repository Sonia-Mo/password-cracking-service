from fastapi import HTTPException, status


class InvalidInputException:
    not_phone_number = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                     detail="Input in not valid - only phone number password is allowed"
                                     )
