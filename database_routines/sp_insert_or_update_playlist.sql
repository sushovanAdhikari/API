CREATE OR REPLACE PROCEDURE public.sp_insert_or_update_playlist(IN ytube_playlist_id text, IN playlist_name character varying, IN channel_owner character varying, IN videos_list jsonb)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    action text;
    v_ytube_playlist_id text := ytube_playlist_id;
    v_playlist_name VARCHAR := playlist_name;
    v_channel_owner VARCHAR := channel_owner;
    v_videos_list jsonb := videos_list;
    v_playlist_id INTEGER; 
    inner_error_message text;
--  videos variable
  	v_ytube_video_id text;
  	v_video_title text;
  	v_video_desc text;
   	v_channel_name varchar;
   	v_channel_id text;
    i_video jsonb;
BEGIN
    -- Check if the record already exists based on a condition (e.g., playlist_id)
    IF not EXISTS (SELECT 1 FROM playlist WHERE playlist.ytube_playlist_id = v_ytube_playlist_id) THEN
        -- Set the action to "update" if the record exists
        action := 'insert';
    END IF;
   
       -- Perform the action based on the variable
	if action = 'insert' THEN
            INSERT INTO playlist(playlist_status, ytube_playlist_id, playlist_name, channel_owner)
            VALUES (1, v_ytube_playlist_id, v_playlist_name, v_channel_owner);
           
           	select playlist_id into v_playlist_id from playlist where playlist.ytube_playlist_id = v_ytube_playlist_id;        
    end if;
   
    insert into video_playlist_log(type, id_for_type) values ('playlist', v_ytube_playlist_id);
--   perform action on videos from here on
   	for i_video in SELECT jsonb_array_elements(v_videos_list)
   	LOOP
   		v_ytube_video_id := i_video->> 'ytube_video_id'::text;
	   	v_video_title    := i_video->> 'video_title'::text;
	    v_video_desc     := i_video->> 'video_description'::text;
	    v_channel_name   := i_video->> 'channel_name'::varchar;
	    v_channel_id     := i_video->> 'channel_id'::text;
   		call sp_insert_or_update_videolist(v_ytube_video_id, v_video_title, v_video_desc, v_channel_name, v_channel_id, v_playlist_id,inner_error_message);
   		
   		IF inner_error_message IS NOT NULL THEN
            -- Handle the error, log it, or take appropriate action
            RAISE NOTICE 'Error from inner stored procedure: %', inner_error_message;
            RAISE exception 'Error from inner stored procedure: %', inner_error_message;
        END IF;
   	end loop;
--	call sp_update_status_removed_content(inner_error_message);
--	
--	IF inner_error_message IS NOT NULL THEN
--            -- Handle the error, log it, or take appropriate action
--            RAISE NOTICE 'Error from inner stored procedure: %', inner_error_message;
--            RAISE exception 'Error from inner stored procedure: %', inner_error_message;
--    END IF;
end;
$procedure$
;
