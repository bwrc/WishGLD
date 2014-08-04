function SO = RecuMergeStruct(A,B)
% RECUMERGESTRUCT recursively merges fields & subfields of structs A and B
% The aim is to produce 1D arrays of every shared field in the structs,
% indexed by the struct identifier, which we assume is a point field 
% somewhere at the top level.
% Scalars are aggregated to vectors, vectors are aggregated if of equal
% size, mxn matrices are placed in cell arrays, as are cells and char
% arrays.
%
% Author:   Benjamin Cowley
% Date:     04.08.2014
% 

    if nargin<2
        return;
    end
    SO=A;
    if isempty(A)
        SO=B;
        return;
    elseif isempty(B)
        return;
    end

    if ismatrix(A) && ismatrix(B)
        numa=numel(A);  numb=numel(B);
        for i=1:min(numa, numb)
            SO(i)=MergeSimple(A(i), B(i));
        end
        if numb>numa
            for j=i:numb
                SO(j)=MergeSimple(A(j), B(j));
            end
        end
    else
        SO=MergeSimple(A,B);
    end
end

function SO=MergeSimple(A,B)

    SO=A;
    try
        fna=fieldnames(A);
        fnb=fieldnames(B);
        if ~isequal(fna, fnb)
            % copy extra fields from B to A
            for i=1:length(fnb)
                fi=fnb{i};
                if ~isfield(A,fi)
                    SO.(fi) = B.(fi);
                end
            end
        end

        for i=1:length(fna)
            fi=fna{i};
            if isfield(B,fi)
                    if isempty(B.(fi))
                        continue;
                    elseif isnumeric(B.(fi)) || islogical(B.(fi))
                        if isvector(B.(fi)) && length(A.(fi))==length(B.(fi))
                            if iscolumn(A.(fi))
                                SO.(fi) = [A.(fi)'; B.(fi)'];
                            else
                                SO.(fi) = [A.(fi); B.(fi)];
                            end
                        else
                            SO.(fi) = {A.(fi); B.(fi)};
                        end
                    elseif iscell(B.(fi)) || ischar(B.(fi))
                        SO.(fi) = {A.(fi); B.(fi)};
                    elseif isstruct(B.(fi))
                        temp=RecuMergeStruct(A.(fi), B.(fi));
                        SO.(fi)=temp;
                    end
            end
        end
    catch ME,
        disp([ME.message ' For: ' fi ';']);
    end

end

