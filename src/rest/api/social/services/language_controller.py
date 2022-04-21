class LanguageController:

    @staticmethod
    def get_field(obj, language='ru'):
        if language == 'ru':
            return obj.native_name
        else:
            return obj.original_name

    @staticmethod
    def get_field_name(language):
        if language == 'ru':
            return 'native_name'
        else:
            return 'original_name'

    @staticmethod
    def get_not_defined(language='ru'):
        if language == 'ru':
            return 'Не указаны'
        else:
            return 'Not defined'
