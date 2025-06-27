from src.project_eval import ProjectEvaluator


def test_evaluator():
    """Test function for the ProjectEvaluator."""
    import os
    import tempfile

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        evaluator = ProjectEvaluator(temp_dir)

        # Test 1: Load non-existent file
        eval_obj, is_valid, error = evaluator.load_evaluation()
        assert eval_obj is None
        assert not is_valid
        assert "does not exist" in error
        print("✓ Test 1 passed: Non-existent file handling")

        # Test 2: Create and save default evaluation
        default_eval = evaluator.create_default_evaluation()
        success = evaluator.save_evaluation(default_eval)
        assert success
        assert evaluator.evaluation_file_path.exists()
        print("✓ Test 2 passed: Default evaluation creation and saving")

        # Test 3: Load saved evaluation
        eval_obj, is_valid, error = evaluator.load_evaluation()
        assert eval_obj is not None
        assert is_valid
        assert error == ""
        print("✓ Test 3 passed: Loading saved evaluation")

        # Test 4: Calculate scores
        scores = evaluator.calculate_scores(default_eval)
        assert scores["main_score"] == 0
        assert scores["final_score"] == 0
        assert scores["percentage"] == 0
        print("✓ Test 4 passed: Score calculation for default evaluation")

        # Test 5: Create evaluation with some scores
        test_eval = evaluator.create_default_evaluation()
        test_eval.structure.architecture_modulaire = 8
        test_eval.structure.lisibilite_code = 4
        test_eval.collaboration.git_utilisation = 7
        test_eval.bonus_ml.choix_modele = 1

        scores = evaluator.calculate_scores(test_eval)
        expected_main = 8 + 4 + 7  # 19
        assert scores["main_score"] == expected_main
        assert scores["bonus_ml_score"] == 1
        assert scores["final_score"] == expected_main + 1
        print("✓ Test 5 passed: Score calculation with non-zero values")

        # Test 6: Generate summary
        summary = evaluator.get_evaluation_summary(test_eval)
        assert "19/100" in summary
        assert "1/5" in summary
        print("✓ Test 6 passed: Summary generation")

        # Test 7: Invalid YAML handling
        # Write invalid YAML
        with open(evaluator.evaluation_file_path, "w") as f:
            f.write("invalid: json: content: [")

        eval_obj, is_valid, error = evaluator.load_evaluation()
        assert eval_obj is None
        assert not is_valid
        assert "YAML parsing error" in error
        print("✓ Test 7 passed: Invalid YAML handling")

        print("\n🎉 All tests passed!")
