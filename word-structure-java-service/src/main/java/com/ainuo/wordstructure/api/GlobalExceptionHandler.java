package com.ainuo.wordstructure.api;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public DataResponse<String> handleIllegalArgument(IllegalArgumentException ex) {
        DataResponse<String> response = new DataResponse<>();
        response.setCode(400);
        response.setMessage(ex.getMessage());
        response.setData(null);
        return response;
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public DataResponse<String> handleAny(Exception ex) {
        DataResponse<String> response = new DataResponse<>();
        response.setCode(500);
        response.setMessage(ex.getMessage());
        response.setData(null);
        return response;
    }
}
