STAGE_RESULT
stage: full_pipeline
status: success
gate_1_verdict: PASS
gate_1_notes: none
gate_2_verdict: PASS
gate_2_notes: STATE6_RIGHT:PASS successors=[10,7,2] probs≈1/3 rewards=0 done_only_7, NO_GOAL15:PASS, SUM_P:PASS 1.0, UNIFORM_POLICY:PASS pi[6][2]=0.25, GAMMA_RETURN:PASS 0.9801, TERMINALS:PASS {5,7,11,12,15}=done terminal_v=0, GEOMETRY:PASS state6=(1,2) neighbors={up:2,down:10,left:5,right:7}, PLAN_CODE:PASS env.unwrapped.P no step/reset/no update
state6_right_successors: [(0.33333333333333337,10,0.0,False),(0.3333333333333333,7,0.0,True),(0.33333333333333337,2,0.0,False)]
plan_md: manim_service/concept_videos/mdp_foundations_plan.md
choreo_md: manim_service/concept_videos/mdp_foundations_choreo.md
scene_py: manim_service/concept_videos/mdp_foundations_concept.py
silent_mp4: backend/media/concept_videos/mdp_foundations_concept.mp4
render_seconds: 78
animations: 86
errors: none