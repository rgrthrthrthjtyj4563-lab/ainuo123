package com.ainuo.wordstructure.domain.repo;

public interface TemplateExtractionRepository {
    Long saveExtraction(String fileName, String fileHash, String structureJson, String status);
}
