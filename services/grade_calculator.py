# grade_calculator.py - formulas for score normalization and grade calculations


class GradeCalculator:
    @staticmethod
    def normalize_score(score: float, max_score: float) -> float:
        # convert raw score to percentage (0 to 100)
        if max_score <= 0:
            raise ValueError(f"Max score must be greater than 0, got {max_score}")
        if score < 0:
            raise ValueError(f"Score cannot be negative, got {score}")
        if score > max_score:
            raise ValueError(f"Score {score} exceeds maximum allowed score {max_score}")
        return (score / max_score) * 100.0

    @classmethod
    def compute_component_total(cls, raw_scores) -> float:
        # compute average percentage across multiple scores in a category
        if not raw_scores:
            return 0.0
        normalized = [cls.normalize_score(s, m) for s, m in raw_scores]
        return sum(normalized) / len(normalized)

    @classmethod
    def compute_period_grade(cls, scores_by_type, weights_by_type) -> float:
        # period grade = sum of (average percentage of each category * weight)
        if not weights_by_type:
            return 0.0

        total_weight = sum(weights_by_type.values())
        if total_weight <= 0:
            raise ValueError("Total weights must be greater than 0")

        period_grade = 0.0
        for comp_type, weight in weights_by_type.items():
            scores = scores_by_type.get(comp_type, [])
            avg_score = cls.compute_component_total(scores) if scores else 0.0
            period_grade += avg_score * (weight / total_weight)

        return round(period_grade, 2)

    @staticmethod
    def compute_final_grade(midterm_grade: float, finals_grade: float, midterm_weight: float = 40.0, finals_weight: float = 60.0) -> float:
        # overall final grade using configured period weights (e.g., 40% midterm + 60% finals)
        total_w = midterm_weight + finals_weight
        if total_w <= 0:
            raise ValueError("Period weights sum must be greater than 0")

        final = (midterm_grade * (midterm_weight / total_w)) + (finals_grade * (finals_weight / total_w))
        return round(final, 2)

    @staticmethod
    def determine_remarks(final_grade: float, passing_grade: float = 75.0) -> str:
        # check if student passed or failed (standard 75.0 passing mark)
        return "PASSED" if final_grade >= passing_grade else "FAILED"

    @staticmethod
    def determine_rating(final_grade: float) -> str:
        # philippine / ndmu collegiate grading scale (1.00 - 5.00)
        # strictly below 75.0 is failing (5.00)
        if final_grade < 75.0:
            return "5.00"
        elif final_grade >= 98.0:
            return "1.00"
        elif final_grade >= 95.0:
            return "1.25"
        elif final_grade >= 92.0:
            return "1.50"
        elif final_grade >= 89.0:
            return "1.75"
        elif final_grade >= 86.0:
            return "2.00"
        elif final_grade >= 83.0:
            return "2.25"
        elif final_grade >= 80.0:
            return "2.50"
        elif final_grade >= 77.0:
            return "2.75"
        elif final_grade >= 75.0:
            return "3.00"
        else:
            return "5.00"
