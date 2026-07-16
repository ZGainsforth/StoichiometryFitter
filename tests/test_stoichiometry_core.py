import json

import StoichiometryCore as core


def test_phase_analyses_are_discovered_outside_config_data():
    options = core.list_config_options()

    assert 'Olivine' in options['phase_analysis']
    assert 'Sheet Silicate Ternary' in options['phase_analysis']
    assert core.phase_analysis_path('Olivine') == 'PhaseAnalysis/Olivine.py'


def test_run_analysis_returns_structured_quantification():
    analysis_input = core.load_input_csv('ConfigData/ExampleInput.csv')
    analysis_input.stoichiometry = core.load_stoichiometry('Silicates')
    options = core.AnalysisOptions(kfactors='Titan 80 keV')

    result = core.run_analysis(analysis_input, options=options)

    table_names = [table.name for table in result.tables]
    assert table_names[:2] == ['input', 'quantification']
    assert result.tables[0].title == 'Input Data'
    assert result.tables[1].title == 'Quantification Results'
    assert result.report_text.startswith('Input data:')
    quant_rows = result.tables[1].rows
    assert any(row['element'] == 'Mg' and row['at_pct'] > 0 for row in quant_rows)
    assert result.quant['Mg']['at_pct'] > 0


def test_run_analysis_can_fit_selected_phases():
    analysis_input = core.load_input_csv('ConfigData/ExampleInput.csv')
    analysis_input.stoichiometry = core.load_stoichiometry('Silicates')
    options = core.AnalysisOptions(
        kfactors='Titan 80 keV',
        selected_phases=['Forsterite (Mg2SiO4)', 'Fayalite (Fe2SiO4)'],
    )

    result = core.run_analysis(analysis_input, options=options)

    tables = {table.name: table for table in result.tables}
    assert 'phase_fit' in tables
    assert 'phase_fit_composition' in tables
    assert tables['phase_fit'].metadata['residual'] >= 0


def test_save_analysis_writes_csv_text_and_json(tmp_path):
    analysis_input = core.load_input_csv('ConfigData/ExampleInput.csv')
    analysis_input.stoichiometry = core.load_stoichiometry('Silicates')
    options = core.AnalysisOptions(kfactors='Titan 80 keV')

    result = core.run_analysis(analysis_input, options=options, save_dir=str(tmp_path), basename='sample')

    saved_paths = result.files
    assert (tmp_path / 'sample.csv').exists()
    assert (tmp_path / 'sample.txt').exists()
    assert (tmp_path / 'sample.json').exists()
    assert saved_paths['results_json'].endswith('sample.json')

    with open(saved_paths['results_json']) as fid:
        payload = json.load(fid)
    assert sorted(payload.keys()) == ['input', 'options', 'schema_version', 'tables', 'text_output']
    assert payload['text_output'].startswith('Input data:')
    assert payload['tables'][0]['name'] == 'input'
    assert payload['tables'][0]['title'] == 'Input Data'
    assert payload['tables'][1]['name'] == 'quantification'
    assert 'report_text' not in payload
    assert 'quant' not in payload
    assert 'phase_analysis' not in payload
    assert 'files' not in payload


def test_saved_json_can_replay_to_identical_json(tmp_path):
    analysis_input = core.load_input_csv('ConfigData/ExampleInput.csv')
    analysis_input.stoichiometry = core.load_stoichiometry('Silicates')
    options = core.AnalysisOptions(
        kfactors='Titan 80 keV',
        selected_phases=['Forsterite (Mg2SiO4)', 'Fayalite (Fe2SiO4)'],
    )

    first = core.run_analysis(analysis_input, options=options, save_dir=str(tmp_path), basename='first')
    second = core.rerun_analysis_from_json(first.files['results_json'], save_dir=str(tmp_path), basename='second')

    with open(first.files['results_json']) as fid:
        first_payload = json.load(fid)
    with open(second.files['results_json']) as fid:
        second_payload = json.load(fid)

    assert first_payload == second_payload


def test_olivine_phase_analysis_writes_structured_tables_to_json(tmp_path):
    analysis_input = core.load_input_csv('ConfigData/ExampleInput.csv')
    analysis_input.stoichiometry = core.load_stoichiometry('Silicates')
    options = core.AnalysisOptions(kfactors='Titan 80 keV', phase_analysis='Olivine')

    result = core.run_analysis(analysis_input, options=options, save_dir=str(tmp_path), basename='olivine')

    tables = {table.name: table for table in result.tables}
    assert 'phase_analysis_olivine_numeric_results' in tables
    assert 'phase_analysis_olivine_cations_per_4_oxygens' in tables
    assert any(row['metric'] == 'Mg/(Mg+Fe)' for row in tables['phase_analysis_olivine_numeric_results'].rows)
    assert any(row['label'] == 'Mg' for row in tables['phase_analysis_olivine_cations_per_4_oxygens'].rows)

    with open(result.files['results_json']) as fid:
        payload = json.load(fid)
    json_tables = {table['name']: table for table in payload['tables']}
    assert json_tables['phase_analysis_olivine_numeric_results']['title'] == 'Olivine Numeric Results'
    assert any(row['metric'] == 'Mg/(Mg+Fe)' for row in json_tables['phase_analysis_olivine_numeric_results']['rows'])
    assert any(row['label'] == 'Mg' for row in json_tables['phase_analysis_olivine_cations_per_4_oxygens']['rows'])

    replay = core.rerun_analysis_from_json(result.files['results_json'], save_dir=str(tmp_path), basename='olivine_replay')
    with open(replay.files['results_json']) as fid:
        replay_payload = json.load(fid)
    assert payload == replay_payload
