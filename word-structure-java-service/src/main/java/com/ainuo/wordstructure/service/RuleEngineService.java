package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.infrastructure.rules.RuleDefinition;
import com.ainuo.wordstructure.infrastructure.rules.RuleLoader;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Locale;
import java.util.regex.Pattern;

@Service
public class RuleEngineService {
    private final RuleLoader ruleLoader;

    public RuleEngineService(RuleLoader ruleLoader) {
        this.ruleLoader = ruleLoader;
    }

    public RuleClassifyResult classify(String title) {
        String normalized = title == null ? "" : title.toLowerCase(Locale.ROOT);
        RuleDefinition rule = ruleLoader.getCurrent().getDefinition();
        if (containsAny(normalized, rule.getFixedContentKeywords())) {
            return new RuleClassifyResult("fixed_content", 0.9, "标题包含固定内容关键词");
        }
        if (containsAny(normalized, rule.getAiChapterKeywords())) {
            return new RuleClassifyResult("ai_chapter", 0.85, "标题包含AI生成章节关键词");
        }
        if (containsAny(normalized, rule.getDataAnalysisKeywords())) {
            return new RuleClassifyResult("data_analysis", 0.8, "标题包含数据分析关键词");
        }
        if (matchesAny(title, rule.getQuestionPatterns())) {
            return new RuleClassifyResult("data_analysis", 0.9, "标题包含明确题号标识");
        }
        return new RuleClassifyResult("container", 0.5, "未匹配到特定规则，默认为容器/通用章节");
    }

    private boolean containsAny(String text, List<String> keywords) {
        if (text == null || keywords == null || keywords.isEmpty()) {
            return false;
        }
        for (String keyword : keywords) {
            if (keyword != null && !keyword.isBlank() && text.contains(keyword.toLowerCase(Locale.ROOT))) {
                return true;
            }
        }
        return false;
    }

    private boolean matchesAny(String text, List<String> patterns) {
        if (text == null || patterns == null || patterns.isEmpty()) {
            return false;
        }
        for (String pattern : patterns) {
            if (pattern != null && !pattern.isBlank() && Pattern.compile(pattern, Pattern.CASE_INSENSITIVE).matcher(text).find()) {
                return true;
            }
        }
        return false;
    }
}
