from flask import jsonify


class ResponseObject(object):
    def __init__(self, status_code, message, data=None, success=True, reason=None):
        self.status_code = status_code
        self.message = message
        self.data = data
        self.reason = None
        self.success = success

    @classmethod
    def bad_request(cls, message='Bad Request', reason=None):
        res = cls(400, message, reason=reason, success=False)
        return res.to_json()

    @classmethod
    def not_found(cls, message='Not Fount', reason=None):
        return cls(404, message, reason=reason, success=False).to_json()

    @classmethod
    def success(cls, message='', data=None):
        return cls(200, message, data=data, success=True).to_json()
    
    @classmethod
    def error(cls, message='Unkonw Error', data=None):
        return cls(500, message, data=data, success=False).to_json()

    def to_json(self):
        return jsonify({
            "code": self.status_code,
            "message": self.message,
            "data": self.data,
            "success": self.success,
            "reason": self.reason
        })
