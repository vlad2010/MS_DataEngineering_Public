
set OUTPUT=Results\Issues_7 
rd %OUTPUT% /s/q

@rem python CheckIssues.py --issues_file ..\Final_Original_Reports\final_40.txt --prompt_file prompt.txt --output_folder %OUTPUT%

python CheckIssues.py --issues_file final_issues7.txt --prompt_file prompt.txt --output_folder %OUTPUT% --src_base_folder d:\GitHub\MS_DataEngineering\Dissertation\Utils\cpp_csharp\



