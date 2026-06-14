package com.example.common.enums;

public enum AdmissionReviewStatus {
    PENDING,
    APPROVED,
    REJECTED;

    public static boolean isValid(String status) {
        if (status == null || status.trim().isEmpty()) {
            return false;
        }
        for (AdmissionReviewStatus value : values()) {
            if (value.name().equals(status.trim().toUpperCase())) {
                return true;
            }
        }
        return false;
    }

    public static String normalize(String status) {
        if (!isValid(status)) {
            return null;
        }
        return status.trim().toUpperCase();
    }
}
