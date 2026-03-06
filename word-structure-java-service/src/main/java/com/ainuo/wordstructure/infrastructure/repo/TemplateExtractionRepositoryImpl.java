package com.ainuo.wordstructure.infrastructure.repo;

import com.ainuo.wordstructure.domain.repo.TemplateExtractionRepository;
import com.ainuo.wordstructure.infrastructure.entity.TemplateExtractionEntity;
import com.ainuo.wordstructure.infrastructure.mapper.TemplateExtractionMapper;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;

@Repository
public class TemplateExtractionRepositoryImpl implements TemplateExtractionRepository {
    private final TemplateExtractionMapper templateExtractionMapper;

    public TemplateExtractionRepositoryImpl(TemplateExtractionMapper templateExtractionMapper) {
        this.templateExtractionMapper = templateExtractionMapper;
    }

    @Override
    public Long saveExtraction(String fileName, String fileHash, String structureJson, String status) {
        TemplateExtractionEntity entity = new TemplateExtractionEntity();
        entity.setFileName(fileName);
        entity.setFileHash(fileHash);
        entity.setExtractedStructure(structureJson);
        entity.setStatus(status);
        entity.setCreatedAt(LocalDateTime.now());
        templateExtractionMapper.insert(entity);
        return entity.getId();
    }
}
