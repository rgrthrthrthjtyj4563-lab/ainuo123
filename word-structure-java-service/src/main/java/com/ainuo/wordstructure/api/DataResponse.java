package com.ainuo.wordstructure.api;

public class DataResponse<T> {
    private Integer code;
    private String message;
    private T data;

    public static <T> DataResponse<T> ok(T data) {
        DataResponse<T> response = new DataResponse<>();
        response.setCode(200);
        response.setMessage("success");
        response.setData(data);
        return response;
    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}
