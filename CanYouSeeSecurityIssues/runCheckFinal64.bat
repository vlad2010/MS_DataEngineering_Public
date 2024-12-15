
set OUTPUT=Results\Test64

rd %OUTPUT% /s/q

python CheckIssues.py --issues_file ..\Final_Original_Reports\final_64.txt --prompt_file prompt.txt --output_folder %OUTPUT% --src_base_folder d:\GitHub\MS_DataEngineering\Dissertation\Utils\cpp_csharp\


