package com.ainuo.wordstructure.infrastructure.rules;

import java.util.ArrayList;
import java.util.List;

public class RuleDefinition {
    private List<String> fixedContentKeywords = new ArrayList<>();
    private List<String> aiChapterKeywords = new ArrayList<>();
    private List<String> dataAnalysisKeywords = new ArrayList<>();
    private List<String> questionPatterns = new ArrayList<>();

    public List<String> getFixedContentKeywords() {
        return fixedContentKeywords;
    }

    public void setFixedContentKeywords(List<String> fixedContentKeywords) {
        this.fixedContentKeywords = fixedContentKeywords;
    }

    public List<String> getAiChapterKeywords() {
        return aiChapterKeywords;
    }

    public void setAiChapterKeywords(List<String> aiChapterKeywords) {
        this.aiChapterKeywords = aiChapterKeywords;
    }

    public List<String> getDataAnalysisKeywords() {
        return dataAnalysisKeywords;
    }

    public void setDataAnalysisKeywords(List<String> dataAnalysisKeywords) {
        this.dataAnalysisKeywords = dataAnalysisKeywords;
    }

    public List<String> getQuestionPatterns() {
        return questionPatterns;
    }

    public void setQuestionPatterns(List<String> questionPatterns) {
        this.questionPatterns = questionPatterns;
    }
}
