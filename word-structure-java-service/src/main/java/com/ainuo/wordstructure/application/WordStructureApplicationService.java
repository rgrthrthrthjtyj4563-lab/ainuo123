package com.ainuo.wordstructure.application;

import com.ainuo.wordstructure.domain.model.ExtractionResult;
import com.ainuo.wordstructure.domain.repo.TemplateExtractionRepository;
import com.ainuo.wordstructure.messaging.ExtractionEventProducer;
import com.ainuo.wordstructure.service.ExtractionPayload;
import com.ainuo.wordstructure.service.WordStructureExtractorService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class WordStructureApplicationService {
    private final WordStructureExtractorService extractorService;
    private final TemplateExtractionRepository templateExtractionRepository;
    private final StringRedisTemplate stringRedisTemplate;
    private final ObjectMapper objectMapper;
    private final ExtractionEventProducer extractionEventProducer;

    public WordStructureApplicationService(
            WordStructureExtractorService extractorService,
            TemplateExtractionRepository templateExtractionRepository,
            StringRedisTemplate stringRedisTemplate,
            ObjectMapper objectMapper,
            ExtractionEventProducer extractionEventProducer
    ) {
        this.extractorService = extractorService;
        this.templateExtractionRepository = templateExtractionRepository;
        this.stringRedisTemplate = stringRedisTemplate;
        this.objectMapper = objectMapper;
        this.extractionEventProducer = extractionEventProducer;
    }

    public ExtractionResult extract(byte[] content, String fileName) {
        ExtractionPayload payload = extractorService.extract(content, fileName);
        String structureJson = serialize(payload.getStructure());
        Long extractionId = templateExtractionRepository.saveExtraction(
                payload.getFileName(),
                payload.getFileHash(),
                structureJson,
                "completed"
        );
        String cacheKey = "word:extract:" + payload.getFileHash();
        stringRedisTemplate.opsForValue().set(cacheKey, structureJson, 10, TimeUnit.MINUTES);
        extractionEventProducer.sendExtractionEvent(extractionId, payload.getFileHash(), payload.getStructure().size());
        ExtractionResult result = new ExtractionResult();
        result.setExtractionId(extractionId);
        result.setFileName(payload.getFileName());
        result.setFileHash(payload.getFileHash());
        result.setStructure(payload.getStructure());
        return result;
    }

    private String serialize(Object data) {
        try {
            return objectMapper.writeValueAsString(data);
        } catch (Exception e) {
            return "[]";
        }
    }
}
