from data_processing.data_access import DataAccessS3


s3_cred = {
    "access_key": "bc03915a4b9f47448e06c064474010b5",
    "secret_key": "ebe9153f8aacbb2dd2244beb9894bac8ec883e6dc42d0dee",
    "cos_url": "https://s3.us-east.cloud-object-storage.appdomain.cloud",
}

s3_conf = {
    "input_folder": "cos-optimal-llm-pile/sanity-test/input/dataset=text/",
    "output_folder": "cos-optimal-llm-pile/boris-test/",
}


def test_table_read_write():
    """
    Testing table read/write
    :return: None
    """
    # create data access
    d_a = DataAccessS3(s3_credentials=s3_cred, s3_config=s3_conf, d_sets=None, checkpoint=False, m_files=-1)
    input_location = "cos-optimal-llm-pile/sanity-test/input/dataset=text/sample1.parquet"
    # read the table
    r_table = d_a.get_table(path=input_location)
    r_columns = r_table.column_names
    print(f"\nnumber of columns in the read table {len(r_columns)}, number of rows {r_table.num_rows}")
    assert 5 == r_table.num_rows
    assert 38 == len(r_columns)
    # get table output location
    output_location = d_a.get_output_location(input_location)
    print(f"Output location {output_location}")
    assert "cos-optimal-llm-pile/boris-test/sample1.parquet" == output_location
    # save the table
    l, result = d_a.save_table(path=output_location, table=r_table)
    print(f"length of saved table {l}, result {result}")
    assert 36132 == l
    s_columns = d_a.get_table(output_location).column_names
    assert len(r_columns) == len(s_columns)
    assert r_columns == s_columns
    # save the table with extended metadata (for lakehouse)
    output_location_wth_schema = "cos-optimal-llm-pile/boris-test/sample1_schema.parquet"
    l, result = d_a.save_table_with_schema(path=output_location_wth_schema, table=r_table)
    print(f"length of saved table with schema {l}, result {result}")
    assert 43779 == l
    s_columns = d_a.get_table(output_location_wth_schema).column_names
    assert len(r_columns) == len(s_columns)
    assert r_columns == s_columns


def test_get_folder():
    """
    Testing get folder
    :return: None
    """
    # create data access
    d_a = DataAccessS3(s3_credentials=s3_cred, s3_config=s3_conf, d_sets=None, checkpoint=False, m_files=-1)
    input_location = "cos-optimal-llm-pile/sanity-test/input/dataset=text/"
    # get the folder
    files = d_a.get_folder_files(path=input_location, extensions=["parquet"])
    print(f"\ngot {len(files)} files")
    assert 1 == len(files)


def test_files_to_process():
    """
    Testing get files to process
    :return: None
    """
    s3_conf = {
        "input_folder": "cos-optimal-llm-pile/bluepile-processing/rel0_7/dedup/",
        "output_folder": "cos-optimal-llm-pile/boris-test/",
    }
    # create data access
    d_a = DataAccessS3(s3_credentials=s3_cred, s3_config=s3_conf, d_sets=None, checkpoint=False, m_files=-1)
    # get files to process
    files, profile = d_a.get_files_to_process()
    print(f"\nfiles {len(files)}, profile {profile}")
    assert 9 == len(files)
    assert 320.3226261138916 == profile["max_file_size"]
    assert 5.962291717529297 == profile["min_file_size"]
    assert 881.4916191101074 == profile["total_file_size"]
    # use checkpoint
    d_a.checkpoint = True
    files, profile = d_a.get_files_to_process()
    print(f"files with checkpointing {len(files)}, profile {profile}")
    assert 8 == len(files)
    assert 182.44072341918945 == profile["max_file_size"]
    assert 5.962291717529297 == profile["min_file_size"]
    assert 561.1689929962158 == profile["total_file_size"]
    # using data sets
    d_a.checkpoint = False
    d_a.d_sets = ["dataset=textbooks"]
    files, profile = d_a.get_files_to_process()
    print(f"using data sets files {len(files)}, profile {profile}")
    assert 9 == len(files)
    assert 320.3226261138916 == profile["max_file_size"]
    assert 5.962291717529297 == profile["min_file_size"]
    assert 881.4916191101074 == profile["total_file_size"]
    # using data sets with checkpointing
    d_a.checkpoint = True
    files, profile = d_a.get_files_to_process()
    print(f"using data sets files {len(files)}, profile {profile}")
    assert 8 == len(files)
    assert 182.44072341918945 == profile["max_file_size"]
    assert 5.962291717529297 == profile["min_file_size"]
    assert 561.1689929962158 == profile["total_file_size"]