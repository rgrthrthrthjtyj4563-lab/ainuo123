package com.ainuo.wordstructure.infrastructure.rules;

import com.ainuo.wordstructure.infrastructure.entity.WordRuleConfigEntity;
import com.ainuo.wordstructure.infrastructure.mapper.WordRuleConfigMapper;
import com.ainuo.wordstructure.util.HashUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

@Component
public class RuleLoader {
    private final ResourceLoader resourceLoader;
    private final WordRuleConfigMapper wordRuleConfigMapper;
    private final StringRedisTemplate stringRedisTemplate;
    private final ObjectMapper objectMapper;
    private final AtomicReference<RuleSnapshot> current = new AtomicReference<>();

    @Value("${word.rules.local-file}")
    private String localFile;
    @Value("${word.rules.redis-key}")
    private String redisKey;

    public RuleLoader(
            ResourceLoader resourceLoader,
            WordRuleConfigMapper wordRuleConfigMapper,
            StringRedisTemplate stringRedisTemplate,
            ObjectMapper objectMapper
    ) {
        this.resourceLoader = resourceLoader;
        this.wordRuleConfigMapper = wordRuleConfigMapper;
        this.stringRedisTemplate = stringRedisTemplate;
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void init() {
        reloadRules();
    }

    @Scheduled(fixedDelayString = "${word.rules.reload-interval-ms:30000}")
    public void reloadRules() {
        RuleDefinition merged = loadMergedDefinition();
        String signature = HashUtil.sha256(serialize(merged));
        RuleSnapshot old = current.get();
        if (old != null && signature.equals(old.getSignature())) {
            return;
        }
        RuleSnapshot snapshot = new RuleSnapshot(signature, merged);
        current.set(snapshot);
        stringRedisTemplate.opsForValue().set(redisKey, serialize(snapshot));
    }

    public RuleSnapshot getCurrent() {
        RuleSnapshot snapshot = current.get();
        if (snapshot != null) {
            return snapshot;
        }
        reloadRules();
        return current.get();
    }

    private RuleDefinition loadMergedDefinition() {
        RuleDefinition base = loadLocalDefinition();
        List<WordRuleConfigEntity> dbRules = loadDbRules();
        for (WordRuleConfigEntity entity : dbRules) {
            List<String> values = splitValues(entity.getRuleValue());
            if ("fixed_content".equals(entity.getRuleType())) {
                base.getFixedContentKeywords().addAll(values);
            } else if ("ai_chapter".equals(entity.getRuleType())) {
                base.getAiChapterKeywords().addAll(values);
            } else if ("data_analysis".equals(entity.getRuleType())) {
                base.getDataAnalysisKeywords().addAll(values);
            } else if ("question_pattern".equals(entity.getRuleType())) {
                base.getQuestionPatterns().addAll(values);
            }
        }
        return base;
    }

    private RuleDefinition loadLocalDefinition() {
        try {
            Resource resource = resourceLoader.getResource(localFile);
            try (InputStream in = resource.getInputStream()) {
                byte[] bytes = in.readAllBytes();
                return objectMapper.readValue(bytes, RuleDefinition.class);
            }
        } catch (Exception ex) {
            RuleDefinition definition = new RuleDefinition();
            definition.setFixedContentKeywords(new ArrayList<>());
            definition.setAiChapterKeywords(new ArrayList<>());
            definition.setDataAnalysisKeywords(new ArrayList<>());
            definition.setQuestionPatterns(new ArrayList<>());
            return definition;
        }
    }

    private List<WordRuleConfigEntity> loadDbRules() {
        try {
            LambdaQueryWrapper<WordRuleConfigEntity> query = new LambdaQueryWrapper<>();
            query.eq(WordRuleConfigEntity::getEnabled, 1);
            return wordRuleConfigMapper.selectList(query);
        } catch (Exception ex) {
            return Collections.emptyList();
        }
    }

    private List<String> splitValues(String value) {
        if (value == null || value.isBlank()) {
            return Collections.emptyList();
        }
        String[] arr = value.split(",");
        List<String> list = new ArrayList<>();
        for (String item : arr) {
            String normalized = item == null ? "" : item.trim();
            if (!normalized.isBlank()) {
                list.add(normalized);
            }
        }
        return list;
    }

    private String serialize(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            return "{}";
        }
    }
}
