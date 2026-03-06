package com.ainuo.wordstructure.infrastructure.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

@TableName("template_extractions")
public class TemplateExtractionEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    @TableField("file_name")
    private String fileName;
    @TableField("file_hash")
    private String fileHash;
    @TableField("extracted_structure")
    private String extractedStructure;
    @TableField("status")
    private String status;
    @TableField("created_at")
    private LocalDateTime createdAt;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getFileHash() {
        return fileHash;
    }

    public void setFileHash(String fileHash) {
        this.fileHash = fileHash;
    }

    public String getExtractedStructure() {
        return extractedStructure;
    }

    public void setExtractedStructure(String extractedStructure) {
        this.extractedStructure = extractedStructure;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
