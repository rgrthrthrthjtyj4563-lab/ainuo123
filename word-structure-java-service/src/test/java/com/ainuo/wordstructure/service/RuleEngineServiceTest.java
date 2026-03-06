package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.infrastructure.rules.RuleDefinition;
import com.ainuo.wordstructure.infrastructure.rules.RuleLoader;
import com.ainuo.wordstructure.infrastructure.rules.RuleSnapshot;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.List;

public class RuleEngineServiceTest {
    private RuleEngineService ruleEngineService;

    @BeforeEach
    void setup() {
        RuleLoader ruleLoader = Mockito.mock(RuleLoader.class);
        RuleDefinition definition = new RuleDefinition();
        definition.setFixedContentKeywords(List.of("声明"));
        definition.setAiChapterKeywords(List.of("前言", "结论"));
        definition.setDataAnalysisKeywords(List.of("分析", "统计"));
        definition.setQuestionPatterns(List.of("Q\\d+", "第\\d+题"));
        Mockito.when(ruleLoader.getCurrent()).thenReturn(new RuleSnapshot("sig", definition));
        ruleEngineService = new RuleEngineService(ruleLoader);
    }

    @Test
    void shouldClassifyFixedContent() {
        RuleClassifyResult result = ruleEngineService.classify("版权声明");
        Assertions.assertEquals("fixed_content", result.getNodeType());
    }

    @Test
    void shouldClassifyDataAnalysisByPattern() {
        RuleClassifyResult result = ruleEngineService.classify("第12题 用药行为");
        Assertions.assertEquals("data_analysis", result.getNodeType());
    }
}
