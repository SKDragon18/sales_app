class ApiResponse:
    @staticmethod
    def success(message="success",data=None):
        return {
            "status":"success",
            "message":message,
            "data":data
        }
    
    @staticmethod
    def fail(message="fail", error=None):
        return{
            "status":"fail",
            "message":message,
            "error":error
        }