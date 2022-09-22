from fastapi import HTTPException, status


class InvalidInputException:
    not_phone_number = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                     detail="Input is not valid - only phone number password is allowed"
                                     )

    empty_file = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                               detail="Input is not valid - file is empty!"
                               )

    not_MD5_hash = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                 detail="Input is not valid - only MD5 hashes are acceptable"
                                 )

    wrong_file_format = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                      detail="Input is not valid - only txt files are allowed"
                                      )
