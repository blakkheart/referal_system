from auth.model import User
import auth.schemas as schemas


async def form_user_profile(user: User) -> schemas.User:
    """
    Функция для формирования профиля пользователя.
    Добавляет юзеру всех, кто воспользовался его кодом.
    """

    user_to_return: dict = {
        'id': user.id,
        'phone_number': user.phone_number,
        'invite_code': user.invite_code,
        'used_code': user.used_code,
    }
    list_of_refferals_to_unpack: list[User] = await user.used_invite_code
    list_of_refferals: list = []
    for usr in list_of_refferals_to_unpack:
        list_of_refferals.append(usr.phone_number)
    user_to_return['list_of_refferals'] = list_of_refferals
    return user_to_return


async def correct_phone_number(phone_number: str) -> str:
    """Функция для формирования телефонного номера для БД."""

    user_phone_number = phone_number
    user_phone_number = (
        '8' + user_phone_number.translate(str.maketrans('', '', ' -()+'))[1:]
    )
    return user_phone_number
